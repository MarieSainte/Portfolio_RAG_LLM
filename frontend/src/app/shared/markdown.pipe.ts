import { Pipe, PipeTransform } from '@angular/core';
import { marked } from 'marked';

/**
 * Convertit du Markdown en HTML.
 * Le HTML est ensuite assaini automatiquement par Angular au binding [innerHTML]
 * (SecurityContext.HTML : scripts et attributs dangereux supprimés).
 * Pipe pur : le rendu n'est recalculé que si le texte change.
 */
@Pipe({ name: 'markdown', standalone: true })
export class MarkdownPipe implements PipeTransform {
  transform(value: string | null | undefined): string {
    if (!value) return '';
    return marked.parse(value, { async: false, gfm: true, breaks: true }) as string;
  }
}
