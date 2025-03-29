# bash ./inference_scripts/run_pipeline.sh
python run_pipeline.py --api_key_yaml_path openai_keys.yaml \
    --model gpt-4o-2024-08-06 \
    --arch openai \
    --file_path x.csv \
    --output_path x.csv