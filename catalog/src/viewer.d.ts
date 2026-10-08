export class MissingFileError extends Error {}

export function prepareSkin(
  dffUrl: string,
  txdUrl: string,
  quality: string,
): Promise<unknown>

export class SkinPreview {
  constructor(canvas: HTMLCanvasElement, quality: string)
  show(data: unknown): void
  dispose(): void
}
