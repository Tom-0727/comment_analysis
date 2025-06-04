file="./buffer/B0DC8S2887-US-Reviews-20250521.xlsx"
points_path="./buffer/results/B0DC8S2887-US-Reviews-points.csv"
final_output="./buffer/results/B0DC8S2887-US-Reviews-analyzed.xlsx"

python points_extract.py --api_key_yaml_path openai_keys.yaml \
        --model qwen-plus \
        --arch qwen \
        --criteria standing_desk \
        --template standing_desk \
        --read_mode amz_xlsx \
        --file_path "$file" \
        --output_path "$points_path"\
        --to_translate False\
        --to_inspect False

python data_analyze.py --file_path "$points_path" \
    --output_path "$final_output" \
    --criteria_path ./modules/criterias/standing_desk_criteria.csv