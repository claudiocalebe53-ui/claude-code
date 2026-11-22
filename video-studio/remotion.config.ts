import { Config } from '@remotion/cli/config'

Config.setVideoImageFormat('jpeg')
// Three.js precisa de WebGL: "angle" funciona em servidores sem GPU
Config.setChromiumOpenGlRenderer('angle')
Config.setOverwriteOutput(true)

// Opcional: usar um Chrome já instalado (ex.: em ambientes sem internet)
if (process.env.REMOTION_CHROME) {
  Config.setBrowserExecutable(process.env.REMOTION_CHROME)
}
