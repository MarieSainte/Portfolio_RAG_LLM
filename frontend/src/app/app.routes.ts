import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () => import('./pages/home/home.component').then((m) => m.HomeComponent),
    title: 'Portfolio — Ingénieur IA',
  },
  {
    path: 'projects',
    loadComponent: () =>
      import('./pages/projects/projects.component').then((m) => m.ProjectsComponent),
    title: 'Projets — Portfolio IA',
  },
  {
    path: 'mind-map',
    loadComponent: () =>
      import('./pages/mind-map/mind-map.component').then((m) => m.MindMapComponent),
    title: 'Carte Mentale — Portfolio IA',
  },
  {
    path: 'contact',
    loadComponent: () =>
      import('./pages/contact/contact.component').then((m) => m.ContactComponent),
    title: 'Contact — Portfolio IA',
  },
  {
    path: '**',
    redirectTo: '',
  },
];
