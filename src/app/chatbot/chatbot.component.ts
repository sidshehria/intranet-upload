import { Component, OnInit } from '@angular/core';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';

interface ChatMessage {
  text: string;
  sender: 'user' | 'bot';
}

interface PdfFile {
  name: string;
  path: string;
  fullPath: string;
}

@Component({
  selector: 'app-chatbot',
  templateUrl: './chatbot.component.html',
  styleUrls: ['./chatbot.component.scss']
})
export class ChatbotComponent implements OnInit {

  searchHistory: string[] = [];
  currentMessage: string = '';
  chatMessages: ChatMessage[] = [];
  autoSuggestions: string[] = [];
  pdfSuggestions: PdfFile[] = [];
  allPdfFiles: PdfFile[] = [];

  selectedPdf: PdfFile | null = null;
  selectedPdfUrl: SafeResourceUrl | null = null;

  datasheetData: any = [];

  constructor(private sanitizer: DomSanitizer) { }

  ngOnInit(): void {
    this.generateAutoSuggestions();
    this.addBotMessage('Hello, how can I assist you today?');
  }

  sendMessage(): void {
    const message = this.currentMessage.trim();
    if (message === '') {
      return;
    }
    this.addUserMessage(message);
    this.searchHistory.unshift(message);
    this.currentMessage = '';
    this.generateAutoSuggestions();
    this.respondToMessage(message);
  }

  addUserMessage(text: string): void {
    this.chatMessages.push({ text, sender: 'user' });
  }

  addBotMessage(text: string): void {
    this.chatMessages.push({ text, sender: 'bot' });
  }

  respondToMessage(message: string): void {
    const lowerMsg = message.toLowerCase();

    // Simple keyword matching on datasheet keys and values
    let response = this.findMatchingResponse(lowerMsg);

    if (!response) {
      response = "Sorry, I couldn't find information related to your query. Please try asking about cable construction, fiber characteristics, or cable specifications.";
    }
    this.addBotMessage(response);
  }

  findMatchingResponse(query: string): string | null {
    // Search in datasheetData keys and nested keys for matching keywords
    for (const sectionKey of Object.keys(this.datasheetData.technical_specifications || {})) {
      const section = this.datasheetData.technical_specifications[sectionKey];
      if (typeof section === 'object' && section !== null) {
        for (const key of Object.keys(section)) {
          const value = section[key];
          if (key.toLowerCase().includes(query) || (typeof value === 'string' && value.toLowerCase().includes(query))) {
            return `${key}: ${value}`;
          }
        }
      } else if (typeof section === 'string' && section.toLowerCase().includes(query)) {
        return `${sectionKey}: ${section}`;
      }
    }
    return null;
  }

  generateAutoSuggestions(): void {
    // Extract keys from datasheetData technical_specifications for suggestions
    const suggestionsSet = new Set<string>();
    const techSpecs = this.datasheetData.technical_specifications || {};
    for (const sectionKey of Object.keys(techSpecs)) {
      suggestionsSet.add(sectionKey);
      const section = techSpecs[sectionKey];
      if (typeof section === 'object' && section !== null) {
        for (const key of Object.keys(section)) {
          suggestionsSet.add(key);
        }
      }
    }
    this.autoSuggestions = Array.from(suggestionsSet).slice(0, 10); // limit to 10 suggestions
  }

  onSuggestionClick(suggestion: string): void {
    this.currentMessage = suggestion;
  }

  onSearchInput(event: any): void {
    const query = event.target.value.toLowerCase().trim();
    if (query.length === 0) {
      this.pdfSuggestions = [];
      return;
    }

    // Load PDF files from input_docs
    this.loadPdfFiles();
    
    // Filter PDF files based on search query
    this.pdfSuggestions = this.allPdfFiles.filter(pdf => 
      pdf.name.toLowerCase().includes(query)
    ).slice(0, 5); // Limit to 5 suggestions
  }

  loadPdfFiles(): void {
    // Get PDF files from the actual input_docs folder structure
    this.allPdfFiles = [
      {
        name: '24F,96F MTUA SS LSZH BK - Indoor - AR',
        path: '',
        fullPath: 'input_docs/Datasheet  - 24F,96F MTUA SS LSZH BK - Indoor - AR.pdf'
      },
      {
        name: '2F,4F,8F D UTA AY SS LSZH BK - 8.5MM - KH9M',
        path: '',
        fullPath: 'input_docs/Datasheet - 2F,4F,8F D UTA AY SS LSZH BK - 8.5MM - KH9M.pdf'
      },
      {
        name: '12F,24F D UTA GY SS PE BK - 8.5MM',
        path: '',
        fullPath: 'input_docs/Datasheet - 12F,24F D UTA GY SS PE BK - 8.5MM.pdf'
      },
      {
        name: '24,48,96F MT UA DS LSZH GY PE',
        path: '',
        fullPath: 'input_docs/Datasheet - 24,48,96F MT UA DS LSZH GY PE  .pdf'
      },
      {
        name: '144F A1 & D MT MICRO SS PE BK - 7.9 mm',
        path: '',
        fullPath: 'input_docs/Datasheet - 144F A1 & D MT MICRO SS PE BK - 7.9 mm.pdf'
      },
      {
        name: '288F MT MICRO SS LSZH BK - 8.0 mm - 12FT',
        path: '',
        fullPath: 'input_docs/Datasheet - 288F  MT MICRO SS LSZH BK - 8.0 mm - 12FT.pdf'
      }
    ];
  }

  openPdfFile(pdf: PdfFile): void {
    // Build a path that Angular will serve
    // Remove 'input_docs/' prefix and prepend 'assets/input_docs/' for correct URL
    const relativePath = pdf.fullPath.replace(/^input_docs\//, '');
    const fileUrl = `/assets/input_docs/${relativePath}`;

    this.selectedPdf = pdf;
    // this.selectedPdfUrl = this.sanitizer.bypassSecurityTrustResourceUrl(fileUrl
    this.selectedPdfUrl = fileUrl;

    this.addBotMessage(`Opening PDF: ${pdf.name}`);
    this.pdfSuggestions = [];
    this.currentMessage = '';
  }
}
