# bash ./inference_scripts/run_pipeline.sh
python points_extract.py --api_key_yaml_path openai_keys.yaml \
    --model gpt-4.1-2025-04-14 \
    --arch openai \
    --criteria stations_executive_desk \
    --template desk \
    --read_mode csv \
    --file_path ./results/dummy_data_for_criteria_make.csv \
    --output_path ./results/dummy_data_for_points_extract.csv