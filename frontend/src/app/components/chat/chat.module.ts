import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ChatComponent } from './chat.component';
import { MarkdownModule } from '../../shared/markdown/markdown.module';

@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    MarkdownModule,
    ChatComponent
  ],
  exports: [ChatComponent]
})
export class ChatModule { }
