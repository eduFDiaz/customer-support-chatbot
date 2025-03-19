import { Component, OnInit, NgZone } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';

declare const google: any;

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent implements OnInit {
  constructor(
    private authService: AuthService,
    private router: Router,
    private ngZone: NgZone
  ) {}

  ngOnInit() {
    this.initializeGoogleSignIn();
  }

  async initializeGoogleSignIn() {
    await this.authService.initGoogleAuth();
    
    // Check if Google API is loaded
    if (typeof google !== 'undefined') {
      google.accounts.id.initialize({
        client_id: this.authService.clientId,
        callback: (response: any) => {
          // Need to run in NgZone since Google's callback is outside Angular's zone
          this.ngZone.run(() => {
            this.authService.handleCredentialResponse(response);
          });
        }
      });
      
      google.accounts.id.renderButton(
        document.getElementById('google-signin-button'),
        { 
          theme: 'outline', 
          size: 'large',
          text: 'signin_with',
          shape: 'rectangular',
          width: 250
        }
      );
      
      // Also display the One Tap UI
      google.accounts.id.prompt();
    }
  }
}
