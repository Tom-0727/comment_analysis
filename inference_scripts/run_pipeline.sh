# bash ./inference_scripts/run_pipeline.sh
python run_pipeline.py --api_key_yaml_path openai_keys.yaml \
    --model gpt-4o-2024-08-06 \
    --arch openai \
    --file_path ./docs/amz_reviews_part1.csv \
    --output_path ./results/amz_reviews_part1_output.csv