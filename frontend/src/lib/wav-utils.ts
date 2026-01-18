export function bufferToWav(buffer: AudioBuffer) {
    // Use first channel only for Mono (Whisper works best/fastest with mono)
    const channelData = buffer.getChannelData(0);
    const sampleRate = buffer.sampleRate;
    const length = channelData.length * 2 + 44;
    const buffer_out = new ArrayBuffer(length);
    const view = new DataView(buffer_out);

    let pos = 0;

    function setUint16(data: number) {
        view.setUint16(pos, data, true);
        pos += 2;
    }

    function setUint32(data: number) {
        view.setUint32(pos, data, true);
        pos += 4;
    }

    // write WAVE header
    setUint32(0x46464952); // "RIFF"
    setUint32(length - 8);
    setUint32(0x45564157); // "WAVE"

    setUint32(0x20746d66); // "fmt "
    setUint32(16);
    setUint16(1); // PCM
    setUint16(1); // Mono
    setUint32(sampleRate);
    setUint32(sampleRate * 2); // Byte rate
    setUint16(2); // Block align
    setUint16(16); // Bits per sample

    setUint32(0x61746164); // "data"
    setUint32(length - 44);

    // write data
    for (let i = 0; i < channelData.length; i++) {
        const sample = Math.max(-1, Math.min(1, channelData[i]));
        view.setInt16(pos, (sample < 0 ? sample * 0x8000 : sample * 0x7FFF), true);
        pos += 2;
    }

    return new Blob([buffer_out], { type: "audio/wav" });
}
