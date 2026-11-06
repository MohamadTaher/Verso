/**
 * The short Spanish story bundled in web/public/samples, selected for every new
 * visitor so the app can be tried without an EPUB to hand.
 */
const SAMPLE_PATH = 'samples/sample-book.epub';

export const SAMPLE_NAME = 'El farero de Isla Gris (sample).epub';

/**
 * Its source language, set for the reader because Spanish is written in the
 * Latin alphabet and so cannot be detected from the book.
 */
export const SAMPLE_LANGUAGE = 'spanish';

// Remembered by identity rather than by name, so a reader's own book that happens
// to share the filename is never mistaken for the sample.
const samples = new WeakSet<File>();

export function isSampleBook(file: File | null): boolean {
  return file !== null && samples.has(file);
}

export async function fetchSampleBook(): Promise<File> {
  const response = await fetch(`${import.meta.env.BASE_URL}${SAMPLE_PATH}`);
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  const file = new File([await response.blob()], SAMPLE_NAME, { type: 'application/epub+zip' });
  samples.add(file);
  return file;
}
