import { Component, OnInit } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { TranslateService } from '@ngx-translate/core';
import { NavbarComponent } from './shared/navbar/navbar.component';
import { FooterComponent } from './shared/footer/footer.component';
import { ThemeService } from './core/services/theme.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, NavbarComponent, FooterComponent],
  template: `
    <div class="grid-bg"></div>
    <div class="orb orb--1"></div>
    <div class="orb orb--2"></div>
    <app-navbar />
    <main class="main-content">
      <router-outlet />
    </main>
    <app-footer />
  `,
  styles: [`
    .main-content {
      min-height: 100vh;
      padding-top: var(--navbar-height);
    }
  `],
})
export class App implements OnInit {
  constructor(
    private translate: TranslateService,
    private themeService: ThemeService
  ) {}

  ngOnInit(): void {
    const savedLang = localStorage.getItem('lang') || 'fr';
    this.translate.use(savedLang);
  }
}
