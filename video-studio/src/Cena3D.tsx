import { Audio } from '@remotion/media'
import { ThreeCanvas } from '@remotion/three'
import {
  AbsoluteFill,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion'
import { Legendas } from './Legendas'

const Cubo = () => {
  const frame = useCurrentFrame()
  const { fps } = useVideoConfig()
  const escala = spring({ frame, fps, config: { damping: 12 } })
  const rot = interpolate(frame, [0, 150], [0, Math.PI * 2])
  return (
    <mesh rotation={[rot * 0.5, rot, 0]} scale={escala * 1.6}>
      <boxGeometry args={[1, 1, 1]} />
      <meshStandardMaterial color="#D77757" metalness={0.3} roughness={0.4} />
    </mesh>
  )
}

export const Cena3D = () => {
  const { width, height } = useVideoConfig()
  return (
    <AbsoluteFill style={{ backgroundColor: '#1f1b18' }}>
      <ThreeCanvas width={width} height={height} camera={{ position: [0, 0, 5] }}>
        <ambientLight intensity={0.4} />
        <directionalLight position={[3, 4, 5]} intensity={2} />
        <Cubo />
      </ThreeCanvas>
      <Audio src={staticFile('audio.mp3')} />
      <Legendas />
    </AbsoluteFill>
  )
}
