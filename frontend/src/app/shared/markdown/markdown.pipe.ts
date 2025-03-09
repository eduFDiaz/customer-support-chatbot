import { Pipe, PipeTransform } from '@angular/core';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { marked } from 'marked';

@Pipe({
  name: 'markdown'
})
export class MarkdownPipe implements PipeTransform {
  
  constructor(private sanitizer: DomSanitizer) {}
  
  transform(value: string): SafeHtml {
    if (!value) {
      return '';
    }
    
    const htmlContent: string = marked(value) as string;
    return this.sanitizer.bypassSecurityTrustHtml(htmlContent);
  }
}
