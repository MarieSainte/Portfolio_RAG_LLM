import { Injectable, signal, effect } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class ThemeService {
  private readonly THEME_KEY = 'portfolio-theme';
  isDarkMode = signal<boolean>(this.getInitialTheme());

  constructor() {
    effect(() => {
      const mode = this.isDarkMode();
      if (mode) {
        document.body.classList.remove('light-mode');
        localStorage.setItem(this.THEME_KEY, 'dark');
      } else {
        document.body.classList.add('light-mode');
        localStorage.setItem(this.THEME_KEY, 'light');
      }
    });
  }

  toggleTheme() {
    this.isDarkMode.update(dark => !dark);
  }

  private getInitialTheme(): boolean {
    const saved = localStorage.getItem(this.THEME_KEY);
    if (saved) return saved === 'dark';
    return !window.matchMedia('(prefers-color-scheme: light)').matches;
  }
}
