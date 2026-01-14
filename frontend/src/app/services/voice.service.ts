import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { environment } from '../../environments/environment';

export interface STTResult {
  text: string;
  confidence: number;
}

export interface TTSOptions {
  voice?: string;
  language?: string;
  speed?: number;
}

@Injectable({
  providedIn: 'root'
})
export class VoiceService {
  private readonly API_BASE = `${environment.apiUrl || 'http://localhost:8000'}/api/voice`;

  constructor(private http: HttpClient) {}

  /**
   * Convert speech audio to text
   * @param audioBlob The recorded audio blob
   * @returns Observable with transcription result
   */
  stt(audioBlob: Blob): Observable<STTResult> {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.webm');

    return this.http.post<STTResult>(`${this.API_BASE}/stt`, formData).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Convert text to speech audio
   * @param text The text to convert to speech
   * @param options TTS configuration options
   * @returns Observable with audio blob
   */
  tts(text: string, options?: TTSOptions): Observable<Blob> {
    const payload = {
      text,
      voice: options?.voice || 'en-US-Neural2-D',
      language: options?.language || 'en-US',
      speed: options?.speed || 1.0
    };

    return this.http.post(`${this.API_BASE}/tts`, payload, {
      responseType: 'blob',
      headers: {
        'Content-Type': 'application/json'
      }
    }).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Get available voices for TTS
   * @returns Observable with list of available voices
   */
  getAvailableVoices(): Observable<any[]> {
    return this.http.get<any[]>(`${this.API_BASE}/voices`).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Check if voice features are supported
   * @returns Object with support status
   */
  checkSupport(): {
    mediaRecorder: boolean;
    getUserMedia: boolean;
    audioContext: boolean;
  } {
    return {
      mediaRecorder: typeof MediaRecorder !== 'undefined',
      getUserMedia: !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia),
      audioContext: typeof AudioContext !== 'undefined' || typeof (window as any).webkitAudioContext !== 'undefined'
    };
  }

  /**
   * Request microphone permission
   * @returns Promise that resolves if permission granted
   */
  async requestMicrophonePermission(): Promise<boolean> {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      // Stop the stream immediately after getting permission
      stream.getTracks().forEach(track => track.stop());
      return true;
    } catch (error) {
      console.error('Microphone permission denied:', error);
      return false;
    }
  }

  /**
   * Play audio blob
   * @param audioBlob The audio blob to play
   * @returns Promise that resolves when audio finishes playing
   */
  async playAudio(audioBlob: Blob): Promise<void> {
    return new Promise((resolve, reject) => {
      const audio = new Audio();
      const url = URL.createObjectURL(audioBlob);

      audio.src = url;
      audio.onended = () => {
        URL.revokeObjectURL(url);
        resolve();
      };
      audio.onerror = (error) => {
        URL.revokeObjectURL(url);
        reject(error);
      };

      audio.play().catch(reject);
    });
  }

  private handleError(error: HttpErrorResponse) {
    let errorMessage = 'An unknown error occurred';

    if (error.error instanceof ErrorEvent) {
      // Client-side error
      errorMessage = error.error.message;
    } else {
      // Server-side error
      if (error.status === 0) {
        errorMessage = 'Unable to connect to voice service';
      } else if (error.status === 400) {
        errorMessage = 'Invalid audio file or request';
      } else if (error.status === 413) {
        errorMessage = 'Audio file too large';
      } else if (error.status === 415) {
        errorMessage = 'Unsupported audio format';
      } else if (error.status === 429) {
        errorMessage = 'Too many requests. Please wait and try again.';
      } else if (error.status === 503) {
        errorMessage = 'Voice service temporarily unavailable';
      } else {
        errorMessage = error.error?.message || `Server error: ${error.status}`;
      }
    }

    console.error('Voice service error:', error);
    return throwError(() => new Error(errorMessage));
  }
}