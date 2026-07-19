import { Component, HostListener, OnInit } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { CommonModule } from '@angular/common';
import { ThemeService } from '../../core/services/theme.service';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [RouterLink, RouterLinkActive, TranslateModule, CommonModule],
  template: `
    <nav class="navbar" [class.navbar--scrolled]="isScrolled">
      <div class="container">
        <div class="navbar__inner">
          <!-- Logo -->
          <a routerLink="/" class="navbar__logo">
            <span class="navbar__logo-bracket">&lt;</span>
            <span class="navbar__logo-initials">AI</span>
            <span class="navbar__logo-bracket">/&gt;</span>
          </a>

          <!-- Desktop Nav -->
          <ul class="navbar__links" [class.navbar__links--open]="isMenuOpen">
            <li>
              <a routerLink="/" routerLinkActive="active" [routerLinkActiveOptions]="{exact: true}"
                 class="navbar__link" (click)="closeMenu()">
                {{ 'NAV.HOME' | translate }}
              </a>
            </li>
            <li>
              <a routerLink="/projects" routerLinkActive="active"
                 class="navbar__link" (click)="closeMenu()">
                {{ 'NAV.PROJECTS' | translate }}
              </a>
            </li>
            <li>
              <a routerLink="/mind-map" routerLinkActive="active"
                 class="navbar__link" (click)="closeMenu()">
                {{ 'NAV.MIND_MAP' | translate }}
              </a>
            </li>
            <li>
              <a routerLink="/contact" routerLinkActive="active"
                 class="navbar__link" (click)="closeMenu()">
                {{ 'NAV.CONTACT' | translate }}
              </a>
            </li>
          </ul>

          <!-- Right Actions -->
          <div class="navbar__actions">
            <!-- Language Switch -->
            <button class="lang-btn" (click)="toggleLang()" [title]="'LANG.SWITCH' | translate">
              <span class="lang-btn__flag">{{ currentLang === 'fr' ? '🇫🇷' : '🇬🇧' }}</span>
              <span class="lang-btn__label">{{ 'LANG.SWITCH' | translate }}</span>
            </button>

            <!-- Theme Toggle -->
            <button class="theme-toggle" (click)="themeService.toggleTheme()" [title]="'THEME.TOGGLE' | translate">
              <span class="theme-toggle__icon" [innerText]="themeService.isDarkMode() ? '🌙' : '☀️'"></span>
            </button>

            <!-- Hamburger Menu -->
            <button class="hamburger" (click)="toggleMenu()" [class.hamburger--open]="isMenuOpen" aria-label="Menu">
              <span></span>
              <span></span>
              <span></span>
            </button>
          </div>
        </div>
      </div>

      <!-- Mobile overlay -->
      <div class="navbar__overlay" [class.navbar__overlay--show]="isMenuOpen" (click)="closeMenu()"></div>
    </nav>
  `,
  styleUrl: './navbar.component.scss',
})
export class NavbarComponent implements OnInit {
  isScrolled = false;
  isMenuOpen = false;
  currentLang = 'fr';

  constructor(
    private translate: TranslateService,
    public themeService: ThemeService
  ) { }

  ngOnInit(): void {
    this.currentLang = localStorage.getItem('lang') || 'fr';
  }

  @HostListener('window:scroll')
  onScroll(): void {
    this.isScrolled = window.scrollY > 20;
  }

  toggleLang(): void {
    this.currentLang = this.currentLang === 'fr' ? 'en' : 'fr';
    this.translate.use(this.currentLang);
    localStorage.setItem('lang', this.currentLang);
  }

  toggleMenu(): void {
    this.isMenuOpen = !this.isMenuOpen;
    document.body.style.overflow = this.isMenuOpen ? 'hidden' : '';
  }

  closeMenu(): void {
    this.isMenuOpen = false;
    document.body.style.overflow = '';
  }
}
