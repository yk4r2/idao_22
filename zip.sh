if [[ -f "submission.csv" ]]; then
    echo " ⚠️ found previously created submission file, deleting."
    echo " it should never be passed along with code "
    rm "submission.csv"
fi
if [[ -f "track_2_submission.zip" ]]; then
    echo " deleting previously archieved submission "  
    rm "track_2_submission.zip"
fi

# script helper for zipping submission
zip -r track_2_submission.zip * -x "env/*" -x "__pycache__/*" -x ".vscode" -x ".DS_Store"
