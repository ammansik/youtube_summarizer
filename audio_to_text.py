import whisper

EOS_TOKENS = [".", "!", "?"]


def transcribe_audio(audio_fpath, max_snt_len=100):
    model = whisper.load_model("small")
    result = model.transcribe(audio_fpath)

    sentences = []
    snt_start = None
    snt = ""
    for segment in result["segments"]:
        snt += f'{segment["text"]} '
        if not snt_start:
            snt_start = segment["start"]
        if (
            segment["text"].strip().split()[-1][-1] in EOS_TOKENS
            or len(snt) > max_snt_len
        ):
            sentences.append(
                {"text": snt.strip(), "start": snt_start, "end": segment["end"]}
            )
            snt_start = None
            snt = ""

    if len(snt) > 0:
        sentences.append(
            {"text": snt.strip(), "start": snt_start, "end": segment["end"]}
        )
        snt_start = None
        snt = ""

    timestamped_text = ""
    for sentence in sentences:
        timestamped_text += (
            f'{sentence["start"]} {sentence["end"]} {sentence["text"]}\n'
        )
    return timestamped_text
