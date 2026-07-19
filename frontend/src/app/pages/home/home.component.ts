import { Component } from '@angular/core';
import { TranslateModule } from '@ngx-translate/core';
import { HeroComponent } from './hero/hero.component';
import { SoftSkillsComponent } from './soft-skills/soft-skills.component';
import { TechSkillsComponent } from './tech-skills/tech-skills.component';
import { AboutComponent } from './about/about.component';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [TranslateModule, HeroComponent, SoftSkillsComponent, TechSkillsComponent, AboutComponent],
  template: `
    <div class="page-enter">
      <app-hero />
      <app-about />
      <app-soft-skills />
      <app-tech-skills />
    </div>
  `,
})
export class HomeComponent {}
