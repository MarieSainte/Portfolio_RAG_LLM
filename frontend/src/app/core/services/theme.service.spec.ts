import { TestBed } from '@angular/core/testing';
import { ThemeService } from './theme.service';

describe('ThemeService', () => {
  beforeEach(() => {
    localStorage.clear();
    // matchMedia n'est pas implémenté dans jsdom : on le stubbe
    window.matchMedia = ((query: string) => ({
      matches: false,
      media: query,
      onchange: null,
      addEventListener: () => {},
      removeEventListener: () => {},
      addListener: () => {},
      removeListener: () => {},
      dispatchEvent: () => false,
    })) as unknown as typeof window.matchMedia;
    TestBed.configureTestingModule({});
  });

  it('devrait être créé', () => {
    expect(TestBed.inject(ThemeService)).toBeTruthy();
  });

  it('toggleTheme inverse le mode', () => {
    const service = TestBed.inject(ThemeService);
    const before = service.isDarkMode();
    service.toggleTheme();
    expect(service.isDarkMode()).toBe(!before);
  });
});
