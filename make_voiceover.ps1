$text = @'
Your brand deserves to be remembered.
KAL builds clear identities with quiet confidence.
From logo to visual system, every detail is made to stand out.
KAL Creative Studio.
'@

Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$voice = $synth.GetInstalledVoices() |
  Where-Object { $_.VoiceInfo.Culture.Name -like 'en-*' } |
  Select-Object -First 1
if ($voice) {
  $synth.SelectVoice($voice.VoiceInfo.Name)
}
$synth.Rate = -1
$synth.Volume = 100
$synth.SetOutputToWaveFile((Join-Path (Get-Location) 'KAL_voiceover.wav'))
$synth.Speak($text)
$synth.SetOutputToDefaultAudioDevice()
$synth.Dispose()
