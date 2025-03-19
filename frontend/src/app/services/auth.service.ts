import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { BehaviorSubject } from 'rxjs';

declare const google: any;

export interface UserProfile {
  id: string;
  email: string;
  name: string;
  imageUrl?: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  public clientId = '796427667261-hatk6e46qstmjtfpmuop5pumr8gikhjm.apps.googleusercontent.com'; // Replace with your Google Client ID
  private user = new BehaviorSubject<UserProfile | null>(null);
  public user$ = this.user.asObservable();

  constructor(private router: Router) {
    this.loadGoogleScript();
  }

  private loadGoogleScript() {
    if (!document.getElementById('google-script')) {
      const script = document.createElement('script');
      script.id = 'google-script';
      script.src = 'https://accounts.google.com/gsi/client';
      script.async = true;
      script.defer = true;
      document.body.appendChild(script);
    }
  }

  initGoogleAuth(): Promise<void> {
    return new Promise<void>((resolve) => {
      if (typeof google !== 'undefined') {
        resolve();
      } else {
        window.addEventListener('load', () => {
          resolve();
        });
      }
    });
  }

  handleCredentialResponse(response: any) {
    // Decode the JWT token to get user info
    const responsePayload = this.decodeToken(response.credential);
    
    const user: UserProfile = {
      id: responsePayload.sub,
      email: responsePayload.email,
      name: responsePayload.name,
      imageUrl: responsePayload.picture
    };

    // Store user info
    localStorage.setItem('user', JSON.stringify(user));
    localStorage.setItem('token', response.credential);
    
    this.user.next(user);
    this.router.navigate(['/']);
  }

  decodeToken(token: string) {
    const parts = token.split('.');
    if (parts.length !== 3) {
      throw new Error('Invalid token format');
    }
    const payload = parts[1];
    const base64 = payload.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(atob(base64).split('').map(c => {
      return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));
    
    return JSON.parse(jsonPayload);
  }

  logout() {
    localStorage.removeItem('user');
    localStorage.removeItem('token');
    this.user.next(null);
    this.router.navigate(['/login']);
  }

  isLoggedIn(): boolean {
    return localStorage.getItem('user') !== null;
  }

  getCurrentUser(): UserProfile | null {
    const userData = localStorage.getItem('user');
    return userData ? JSON.parse(userData) : null;
  }
}
