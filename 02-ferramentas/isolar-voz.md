# Isolar a voz (audio-separator + faster-whisper)

> Data: 2026-10-27 · Tipo: guia · Status: vigente

**Resumo:** tira bateria, instrumentos e ruído e deixa só a voz do pregador (audio-separator com o modelo UVR-MDX-NET-Voc_FT), e transcreve com o faster-whisper `small` para achar os momentos e dar o tempo de cada palavra. Usado pela skill `corte-de-pregacao`.

- **Como acessar:** CLI `audio-separator` e biblioteca Python `faster-whisper`. O `preparar_corte.py` chama os dois.
- **Instalação:** `pip install audio-separator[cpu] audioread` (ou `uv sync --extra cpu` no computador do Lukas); `pip install faster-whisper`. Modelo de voz (66 MB): `curl -L -o UVR-MDX-NET-Voc_FT.onnx https://github.com/TRvlvr/model_repo/releases/download/all_public_uvr_models/UVR-MDX-NET-Voc_FT.onnx`. Modelo de transcrição: `huggingface_hub.snapshot_download("Systran/faster-whisper-small")`.
- **Credenciais:** nenhuma.
- **Comandos mais usados:**
  - Voz isolada: `audio-separator audio.wav --model_filename UVR-MDX-NET-Voc_FT.onnx --model_file_dir <pasta-do-modelo> --output_format WAV --output_dir saida --single_stem Vocals`
  - Cortes: `uv run scripts/video/corte_pregacao/preparar_corte.py <pregacao.mp4> <pasta> --trechos "ini:fim" --isolar-voz --modelo-voz <onnx> --transcrever`
- **Pegadinhas:**
  - Separar 90 s de áudio leva ~1,5 min em 4 núcleos; a pregação inteira, ~45 min: separe só os trechos do corte.
  - O modelo baixa de `github.com` (liberado) e a transcrição de `huggingface.co` (liberado). `openaipublic.azureedge.net` (modelo padrão do `openai-whisper`) e `download.pytorch.org` são bloqueados na nuvem.
  - Em pregação já limpa o ganho é pequeno (ruído de fundo −45 dB antes e depois); a faixa "música" pode vazar um pouco de voz. Confira de ouvido.
  - `faster-whisper` 1.2.x com `av` ≥ 16 quebra (`metadata_errors`): fixe `av<16`.
  - O Whisper erra nomes bíblicos e gírias: corrija o texto antes de legendar.
- **Log:** 2026-10-27, audio-separator 0.47.1 e faster-whisper 1.2.1 usados nos cortes 1 e 2 e na análise de 5 referências.
