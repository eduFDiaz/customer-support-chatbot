// frontend/src/app/services/chat.service.ts
import { Injectable } from '@angular/core';
import { Observable, Subject } from 'rxjs';
import { ulid } from 'ulid';

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  public sessionId: string = ulid();
  private wsUrl = `ws://localhost:8000/ws/${this.sessionId}`;

  private socket: WebSocket;
  public messagesSubject = new Subject<string>();

  constructor() {
    this.socket = new WebSocket(this.wsUrl);

    this.socket.onmessage = (event) => {
      console.log('Received message:', event.data);
      this.messagesSubject.next(event.data);
    };
  }

  sendMessage(message: string): void {
    console.log('Sending message:', message);
    this.socket.send(message);
  }

  getMessages(): Observable<string> {
    return this.messagesSubject.asObservable();
  }
}