import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from './services/auth.service';
import { WebSocketService } from './services/websocket.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {
  title = 'GenomeCostTracker';
  isAuthenticated = false;
  sidenavOpened = true;

  constructor(
    private authService: AuthService,
    private router: Router,
    private wsService: WebSocketService
  ) {}

  ngOnInit() {
    this.authService.isAuthenticated$.subscribe(
      isAuth => {
        this.isAuthenticated = isAuth;
        if (isAuth) {
          this.wsService.connect();
        } else {
          this.wsService.disconnect();
        }
      }
    );
  }

  logout() {
    this.authService.logout();
    this.router.navigate(['/login']);
  }

  toggleSidenav() {
    this.sidenavOpened = !this.sidenavOpened;
  }
}