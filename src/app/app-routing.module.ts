import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { ChatbotComponent } from './chatbot/chatbot.component';
import { FileUploadComponent } from './file-upload/file-upload.component';
import { JsonPreviewComponent } from './json-preview/json-preview.component';
import { ChatPreviewComponent } from './chat-preview/chat-preview.component';

const routes: Routes = [
  { path: 'chatbot', component: ChatbotComponent },
   { path: 'chatpreview', component: ChatPreviewComponent},
  { path: 'file-upload', component: FileUploadComponent },
  { path: 'json-preview', component: JsonPreviewComponent },
  { path: '', redirectTo: '/chatbot', pathMatch: 'full' },
  { path: '**', redirectTo: '/chatbot' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
