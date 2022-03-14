if [[ -f "submission.csv" ]]; then
    echo " ⚠️ found previously created submission file, deleting."
    echo " it should never be passed along with code "
    rm "submission.csv"
fi
# скрипт, который архивирует сабмишен, исключая перечисленные папки
zip -r track_2_submission.zip * -x "env/*" -x "__pycache__/*" -x ".vscode" -x ".DS_Store"