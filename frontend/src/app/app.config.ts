import { ApplicationConfig } from '@angular/core';
import { provideRouter } from '@angular/router';

import { routes } from './app.routes';
import { ChatService } from './services/chat.service';
import { provideHttpClient } from '@angular/common/http'; // Import provideHttpClient
import { AuthService } from './services/auth.service';

export const appConfig: ApplicationConfig = {
  providers: [provideRouter(routes), provideHttpClient(), ChatService, AuthService]
};
