# model: gpt-4o-2024-08-06  gpt-4o-mini-2024-07-18  gpt-4.5-preview-2025-02-27
python ./translate.py --api_key_yaml_path ./openai_keys.yaml \
    --model gpt-4o-2024-08-06 \
    --mode one-shot \
    --testset_path ./docs/Comment_Analysis_Testset.csv \
    --version v2_4o
    