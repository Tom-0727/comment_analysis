# model: gpt-4o-2024-08-06  gpt-4o-mini-2024-07-18
# mode: run, run_and_eval
python ./evaluate.py --api_key_yaml_path ./openai_keys.yaml \
    --model gpt-4o-mini-2024-07-18 \
    --mode run_and_eval \
    --testset_path ./docs/Comment_Analysis_Testset.csv \
    --version v0_4o_mini