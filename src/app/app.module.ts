import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { ChatbotComponent } from './chatbot/chatbot.component';
import { FileUploadComponent } from './file-upload/file-upload.component';
import { JsonPreviewComponent } from './json-preview/json-preview.component';
import { Routes } from '@angular/router';
import { SafeUrlPipe } from './safe-url.pipe';
import { ChatPreviewComponent } from './chat-preview/chat-preview.component';
const appRoutes: Routes = [
  { path: 'chatpreview', component: ChatPreviewComponent },
  { path: 'chatbot', component: ChatbotComponent },
  { path: 'fileupload', component: FileUploadComponent },
  { path: 'json-preview', component: JsonPreviewComponent }
];

@NgModule({
  declarations: [
    AppComponent,
    ChatbotComponent,
    FileUploadComponent,
    JsonPreviewComponent,
    SafeUrlPipe,
    ChatPreviewComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    FormsModule,
    HttpClientModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }