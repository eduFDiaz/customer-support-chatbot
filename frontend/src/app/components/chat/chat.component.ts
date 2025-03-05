import { Component, OnInit } from '@angular/core';
import { ChatService } from '../../services/chat.service';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

interface Message {
  type: string | 'AI' | 'HUMAN';
  content: string;
}

const EMPTY_MESSAGE = { type: 'HUMAN', content: '' };

@Component({
  selector: 'app-chat',
  standalone: true,
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.scss'],
  imports: [CommonModule, FormsModule], // Add HttpClientModule here
})
export class ChatComponent implements OnInit {
  messages: Message[] = [
    // { type: 'AI', content: 'Hello! How  it going?' },
    // { type: 'HUMAN', content: 'How can I help you today?' },
    // { type: 'AI', content: 'What can I do for you?' },
  ];
  newMessage: Message = { ...EMPTY_MESSAGE };
  inputDisabled:Boolean = false;

  constructor(private chatService: ChatService) {}

  ngOnInit(): void {
    this.loadMessages();
  }

  loadMessages(): void {
    this.chatService.messagesSubject.subscribe((data: any) => {
      this.messages.push({ type: 'AI', content: data });
      this.inputDisabled = false;
    });
  }

  sendMessage(): void {
    if (this.newMessage.content.trim()) {
      this.messages.push({ type: 'HUMAN', content: this.newMessage.content });
      this.chatService.sendMessage(this.newMessage.content);
      this.newMessage = { ...EMPTY_MESSAGE };
      this.inputDisabled = true;
    }
  }
}