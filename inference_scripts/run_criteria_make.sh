# bash ./inference_scripts/run_criteria_make.sh
python criteria_make.py --api_key_yaml_path openai_keys.yaml \
    --model gpt-4.1-2025-04-14 \
    --arch openai \
    --template desk \
    --read_mode csv \
    --file_path ./docs/dummy_data_for_criteria_make.csv \
    --output_path ./results/dummy_data_for_criteria_make.csv