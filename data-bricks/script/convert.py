def convert_vtt_to_txt(vtt_path, txt_path):
    with open(vtt_path, 'r', encoding='utf-8') as vtt_file:
        lines = vtt_file.readlines()

    script_lines = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("NOTE") or "-->" in line:
            continue
        script_lines.append(line)

    # Merge lines into paragraphs
    merged_script = ' '.join(script_lines)

    with open(txt_path, 'w', encoding='utf-8') as txt_file:
        txt_file.write(merged_script)

# Example usage
convert_vtt_to_txt('input.vtt', 'output.txt')
