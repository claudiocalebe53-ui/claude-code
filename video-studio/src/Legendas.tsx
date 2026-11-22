import { type Caption, createTikTokStyleCaptions } from '@remotion/captions'
import { useMemo } from 'react'
import { AbsoluteFill, Sequence, useVideoConfig } from 'remotion'
import legendas from '../public/legendas.json'

const Pagina = ({ texto }: { texto: string }) => (
  <AbsoluteFill style={{ justifyContent: 'flex-end', alignItems: 'center', paddingBottom: 60 }}>
    <div
      style={{
        fontFamily: 'sans-serif',
        fontSize: 56,
        fontWeight: 800,
        color: 'white',
        textShadow: '0 4px 12px rgba(0,0,0,0.8)',
      }}
    >
      {texto}
    </div>
  </AbsoluteFill>
)

export const Legendas = () => {
  const { fps } = useVideoConfig()
  const { pages } = useMemo(
    () =>
      createTikTokStyleCaptions({
        captions: legendas as Caption[],
        combineTokensWithinMilliseconds: 1200,
      }),
    [],
  )
  return (
    <>
      {pages.map((p) => (
        <Sequence
          key={p.startMs}
          from={Math.round((p.startMs / 1000) * fps)}
          durationInFrames={Math.max(1, Math.round((p.durationMs / 1000) * fps))}
        >
          <Pagina texto={p.text} />
        </Sequence>
      ))}
    </>
  )
}
