import { Component, OnInit } from '@angular/core';
import { ChatService } from '../../services/chat.service';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { MarkdownModule } from "../../shared/markdown/markdown.module"; // Import HttpClientModule
import { AuthService } from '../../services/auth.service';
import { UserProfile } from '../../services/auth.service';

export interface Message {
  type: string | 'AI' | 'HUMAN';
  message: string;
}

@Component({
  selector: 'app-chat',
  standalone: true,
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.scss'],
  imports: [CommonModule, FormsModule, HttpClientModule, MarkdownModule], // Add HttpClientModule here
})
export class ChatComponent implements OnInit {
  messages: Message[] = [];
  newMessage: string = '';
  interruptMessage: any = null;
  interruptResponse: string = ''; // Add this variable
  user: UserProfile | null = null;

  constructor(private chatService: ChatService, private authService: AuthService) {}

  ngOnInit(): void {
    this.loadUser();
    this.loadMessages();
    this.handleInterrupts();
  }

  loadUser(): void {
    this.user = this.authService.getCurrentUser();
    if (this.user !== null) {
      this.chatService.initializeWebSocket(this.user);
    } 
  }

  loadMessages(): void {
    this.chatService.getMessages().subscribe((data: any) => {
      this.messages.push({ type: 'AI', message: data });
    });
  }

  handleInterrupts(): void {
    this.chatService.getInterrupts().subscribe((data: any) => {
      this.interruptMessage = data;
    });
  }

  sendMessage(): void {
    if (this.newMessage.trim()) {
      this.messages.push({ type: 'HUMAN', message: this.newMessage });
      this.chatService.sendMessage(this.newMessage);
      this.newMessage = '';
    }
  }

  sendInterruptResponse(response: string): void {
    this.chatService.sendInterruptResponse(response);
    this.interruptMessage = null;
    this.interruptResponse = ''; // Reset the interruptResponse
  }
}