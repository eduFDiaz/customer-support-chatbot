import { Routes } from '@angular/router';
import { ChatComponent } from './components/chat/chat.component';
import { LoginComponent } from './components/login/login.component';
import { authGuard } from './guards/auth.guard';

export const routes: Routes = [
    {
        path: '', 
        component: ChatComponent,
        canActivate: [() => authGuard()]
    },
    {
        path: 'login', 
        component: LoginComponent
    }
];
