"""Utilities for dataset preprocessing.

Includes the DataSetsLoader class and some helper functions.
"""

from dataclasses import dataclass
from typing import Callable, Dict, List, Tuple

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from pandas import DataFrame, Series


def log_return(series: Series) -> Series:
    """Get diff of shifted log from Series."""
    return np.log(series).diff()


def realized_volatility(series: Series) -> Series:
    """Get realized volatility of series."""
    return np.sqrt(np.sum(series ** 2))


def unique_counter(series):
    """Count unique values."""
    return len(np.unique(series))


# thank you, stackoverflow
def RMSPE(y_true: Series, y_pred: Series) -> Series:
    """Calculate the root mean square percentage error."""
    return np.sqrt(np.mean(np.square((y_true - y_pred) / y_true)))


@dataclass(init=True)
class DataSetsLoader:
    """Class to load and preprocess your data.

    I'm too lazy to formalize it in Google codestyle.
    """

    data_path: str
    book_features: Dict[str, List[Callable]]
    trade_features: Dict[str, List[Callable]]
    train: DataFrame = None
    test: DataFrame = None

    def calc_wap(self, df: DataFrame, n: int) -> Series:
        """Get n'th WAP from the DataFrame.

        Arguments:
            - df: pandas.DataFrame with size and price of bid and ask columns,
            - n: int, showing which ask and bid to use.

        Returns:
            - Series: weighted average price of n'th bid and ask.
        """
        bid_ask = df['bid_price{}'.format(n)] * df['ask_size{}'.format(n)]
        ask_bid = df['ask_price{}'.format(n)] * df['bid_size{}'.format(n)]
        bid_and_ask = df['bid_size{}'.format(n)] + df['ask_size{}'.format(n)]
        return (bid_ask + ask_bid) / bid_and_ask

    def price_spread(self, df: DataFrame, n: int) -> Series:
        """Get n'th prices spread from DataFrame.

        Arguments:
            - df: pandas.DataFrame with price of bid and ask columns,
            - n: int, showing which ask and bid to use.

        Returns:
            - Series: weighted average price of n'th bid and ask.
        """
        spread = df['ask_price{}'.format(n)] - df['bid_price{}'.format(n)]
        interval = (df['ask_price{}'.format(n)] + df['bid_price{}'.format(n)]) / 2
        return spread / interval

    def volume_imbalance(self, df: DataFrame) -> Series:
        """Get absolute value of imbalanse from asks to bids."""
        ask_sizes = df['ask_size1'] + df['ask_size2']
        bid_sizes = df['bid_size1'] + df['bid_size2']
        return abs(ask_sizes - bid_sizes)

    def total_volume(self, df: DataFrame) -> Series:
        """Get total volume of asks and bids."""
        ask_sizes = df['ask_size1'] + df['ask_size2']
        bid_sizes = df['bid_size1'] + df['bid_size2']
        return ask_sizes + bid_sizes

    def book_stats_calculator_step(self, df: DataFrame, n: int) -> DataFrame:
        """Calculate n'th statistics for the DataFrame.

        Arguments:
            - df: pandas.DataFrame for which the statistics are calculated,
            - n: int, showing which ask and bid to use.

        Returns:
            - DataFrame: a dataframe with new statics.
        """
        df['wap{}'.format(n)] = self.calc_wap(df, n)
        df['log_return{}'.format(n)] = df.groupby(['time_id'])['wap{}'.format(n)].apply(
            log_return
        )
        df['price_spread{}'.format(n)] = self.price_spread(df, n)
        return df

    def book_stats_calculator(self, df: DataFrame) -> DataFrame:
        """Calculate all the statistics for the orders book."""
        for index in {1, 2}:
            df = self.book_stats_calculator_step(df, index)
        df['wap_balance'] = abs(df['wap1'] - df['wap2'])
        df['ask_spread'] = df['ask_price1'] - df['ask_price2']
        df['bid_spread'] = df['bid_price1'] - df['bid_price2']
        df['volume_imbalance'] = self.volume_imbalance(df)
        df['total_volume'] = self.total_volume(df)
        return df

    def trade_stats_calculator(self, df: DataFrame) -> DataFrame:
        """Calculate all the statistics for the trades book."""
        df['log_return'] = df.groupby('time_id')['price'].apply(log_return)
        return df

    def stats_window_function(
        self,
        df: DataFrame,
        features: Dict[str, List[Callable]],
        seconds_in_bucket: int,
        add_suffix: bool = True,
    ) -> DataFrame:
        """Stats calculator by window.

        Window is a part of the given dataframe that is
        greater or equal than seconds_in_bucket.

        Arguments:
            - df: pandas.DataFrame for which we calculate the features,
            - features: aggregation dict of features and functions,
            - seconds_in_bucket: threshold for the window,
            - add_suffix: whether to add suffix to columns or not.

        Returns:
            - DataFrame: a pandas.DataFrame of aggregated by window features.
        """
        df_feature = df[df['seconds_in_bucket'] >= seconds_in_bucket]
        df_feature = df_feature.groupby(['time_id']).agg(features).reset_index()
        df_feature.columns = ['_'.join(col) for col in df_feature.columns]
        if add_suffix:
            df_feature = df_feature.add_suffix('_' + str(seconds_in_bucket))
        return df_feature

    def features_by_seconds(
        self,
        df: DataFrame,
        features: Dict[str, List[Callable]],
    ) -> DataFrame:
        """Get time-dependent statistics.

        Get stats from {0, 150, 300, 450} to the bucket end.

        Arguments:
            - df: pandas.DataFrame to calculate statistics on,
            - features: aggregation dict of features and functions.

        Returns:
            - DataFrame: a dataframe with calculated time-dependent features.
        """
        df_features = self.stats_window_function(df, features, 0, add_suffix=False)
        for secs in {150, 300, 450}:
            secs_time = 'time_id__{}'.format(secs)
            df_merged = self.stats_window_function(df, features, secs)
            df_features = df_features.merge(
                df_merged, how='left', left_on='time_id_', right_on=secs_time
            )
            df_features.drop('time_id__{}'.format(secs), axis=1, inplace=True)
        return df_features

    def book_preprocessor(self, path: str) -> DataFrame:
        """Preprocess market book parquet."""
        df = pd.read_parquet(path, engine='pyarrow')
        df = self.book_stats_calculator(df)
        df_features = self.features_by_seconds(df, self.book_features)
        del df
        # row_id's to merge
        stock_id = path.split('=')[1]
        df_features['row_id'] = df_features['time_id_'].apply(
            lambda x: '{}-{}'.format(stock_id, x)
        )
        return df_features.drop('time_id_', axis=1)

    def trade_preprocessor(self, path: str) -> DataFrame:
        """Preprocess trade parquet."""
        df = pd.read_parquet(path, engine='pyarrow')
        df = self.trade_stats_calculator(df)
        df_features = self.features_by_seconds(df, self.trade_features)
        del df
        # row_id's to merge
        df_features = df_features.add_prefix('trade_')
        stock_id = path.split('=')[1]
        df_features['row_id'] = df_features['trade_time_id_'].apply(
            lambda x: '{}-{}'.format(stock_id, x)
        )
        return df_features.drop('trade_time_id_', axis=1)

    def get_time_and_stock(self, df: DataFrame) -> DataFrame:
        """Get grouped stats for your stock_id or time_id."""
        realized_volatility_columns = list(
            filter(lambda x: x.find('realized_volatility') >= 0, df.columns)
        )

        for grouper in {'stock', 'time'}:
            grouper_id = '{}_id'.format(grouper)
            df_grouped = df.groupby(grouper_id)
            df_grouped = df_grouped[realized_volatility_columns].agg(
                [np.mean, np.std, np.max, np.min]
            )
            df_grouped = df_grouped.reset_index()
            df_grouped.columns = ['_'.join(col) for col in df_grouped.columns]
            df_grouped = df_grouped.add_suffix(grouper)
            df = df.merge(
                df_grouped,
                how='left',
                left_on=grouper_id,
                right_on='{}_{}'.format(grouper_id, grouper),
            )
            df.drop('{}_{}'.format(grouper_id, grouper), axis=1, inplace=True)
        return df

    def parallel_df_getter(
        self,
        book_path: str,
        trade_path: str,
        stock_id: int,
    ) -> DataFrame:
        """Getter to pass to joblib."""
        return pd.merge(
            self.book_preprocessor(book_path + str(stock_id)),
            self.trade_preprocessor(trade_path + str(stock_id)),
            on='row_id',
            how='left',
        )

    def preprocessor(
        self,
        path: str,
        stock_ids: list,
        is_train: bool = False,
    ) -> DataFrame:
        """Full dataframes preprocessing cycle."""
        if is_train:
            book_path = '{}book_train.parquet/stock_id='.format(path)
            trade_path = '{}trade_train.parquet/stock_id='.format(path)
        else:
            book_path = '{}book_test.parquet/stock_id='.format(path)
            trade_path = '{}trade_test.parquet/stock_id='.format(path)
        # this Parallel returns list of pd.DataFrames actually
        df = Parallel(n_jobs=-1, verbose=1)(
            delayed(self.parallel_df_getter)(book_path, trade_path, stock_id)
            for stock_id in stock_ids
        )
        return pd.concat(df, ignore_index=True)

    def read_csv_s(self, path: str) -> Tuple[DataFrame, DataFrame]:
        """Read train and test csv's."""
        csv_s = {}
        for csv_type in {'train', 'test'}:
            csv_s[csv_type] = pd.read_csv(
                '{}{}.csv'.format(path, csv_type, csv_type)
            )
            csv_s[csv_type]['row_id'] = (
                csv_s[csv_type].stock_id.astype(str)
                + '-'
                + csv_s[csv_type].time_id.astype(str)
            )
        print('Our training set has {} rows'.format(csv_s['train'].shape[0]))
        return csv_s['train'], csv_s['test']

    def get_datasets(self):
        train, test = self.read_csv_s(self.data_path)
        train_stock_ids = train.stock_id.unique()

        train_ = self.preprocessor(self.data_path, train_stock_ids, is_train=True)
        train = train.merge(train_, on='row_id', how='left')
        del train_

        test_stock_ids = test['stock_id'].unique()
        test_ = self.preprocessor(self.data_path, test_stock_ids, is_train=False)
        test = test.merge(test_, on='row_id', how='left')
        del test_

        self.train = self.get_time_and_stock(train)
        self.test = self.get_time_and_stock(test)


if __name__ == '__main__':
    print('This is a helper library, so just read the code.')
