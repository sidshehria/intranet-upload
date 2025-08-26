import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class SearchService {
  private searchApiUrl = 'https://www.hfcl.com/testapiforsap/api/datasheet/fetchDatasheetSearchResult';


  constructor(private http: HttpClient) { }

  searchDatasheet(searchParams: any): Observable<any> {
    const headers = new HttpHeaders({
      'Content-Type': 'application/json'
    });

    // Build the request payload with required parameters
    const payload = {
      cableID: 0,
      cableDescription: searchParams.cableDescription || "",
      fiberCount: searchParams.fiberCount || "",
      typeofCable: searchParams.typeOfCable || "",
      span: searchParams.span || "",
      tube: searchParams.tube || "",
      tubeColorCoding: searchParams.tubeColorCoding || "",
      fiberType: searchParams.fiberType || "",
      diameter: searchParams.diameter || "",
      tensile: searchParams.tensile || "",
      nescCondition: searchParams.nescCondition || "",
      crush: searchParams.crush || "",
      blowingLength: searchParams.blowingLength || "",
      datasheetURL: searchParams.datasheetURL || "",
      isActive: "Y"
    };

    return this.http.post(this.searchApiUrl, payload, { headers });
  }
}
