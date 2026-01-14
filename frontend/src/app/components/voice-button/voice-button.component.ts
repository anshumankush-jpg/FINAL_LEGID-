import { Component, EventEmitter, Output, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { VoiceService } from '../../services/voice.service';

@Component({
  selector: 'app-voice-button',
  standalone: true,
  imports: [CommonModule],
  template: `
    <button
      class="voice-button"
      [class]="state"
      [disabled]="isDisabled"
      (click)="onButtonClick()"
      [attr.aria-label]="getAriaLabel()"
      type="button"
    >
      <!-- Idle State - Microphone Icon -->
      <div *ngIf="state === 'idle'" class="icon-container">
        <svg class="mic-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
          <path d="M19 10v1a7 7 0 0 1-14 0v-1"></path>
          <line x1="12" y1="19" x2="12" y2="23"></line>
          <line x1="8" y1="23" x2="16" y2="23"></line>
        </svg>
      </div>

      <!-- Recording State - Animated Sound Bars -->
      <div *ngIf="state === 'recording'" class="icon-container">
        <div class="sound-bars">
          <div class="bar" [style.animation-delay]="'0s'"></div>
          <div class="bar" [style.animation-delay]="'0.1s'"></div>
          <div class="bar" [style.animation-delay]="'0.2s'"></div>
          <div class="bar" [style.animation-delay]="'0.3s'"></div>
        </div>
      </div>

      <!-- Processing State - Spinner -->
      <div *ngIf="state === 'processing'" class="icon-container">
        <div class="spinner"></div>
      </div>

      <!-- Error State - Warning Icon -->
      <div *ngIf="state === 'error'" class="icon-container">
        <svg class="warning-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="15" y1="9" x2="9" y2="15"></line>
          <line x1="9" y1="9" x2="15" y2="15"></line>
        </svg>
      </div>
    </button>

    <!-- Recording Duration Indicator -->
    <div *ngIf="state === 'recording' && recordingDuration" class="duration-indicator">
      Listening... {{ recordingDuration }}s
    </div>
  `,
  styleUrls: ['./voice-button.component.css']
})
export class VoiceButtonComponent implements OnInit, OnDestroy {
  @Output() transcribedText = new EventEmitter<string>();
  @Output() transcriptionError = new EventEmitter<string>();

  state: 'idle' | 'recording' | 'processing' | 'error' = 'idle';
  isDisabled = false;
  recordingDuration = 0;
  private recordingStartTime = 0;
  private durationInterval: any;
  private mediaRecorder: MediaRecorder | null = null;
  private audioChunks: Blob[] = [];
  private stream: MediaStream | null = null;

  constructor(private voiceService: VoiceService) {}

  ngOnInit() {
    this.checkMicrophonePermission();
  }

  ngOnDestroy() {
    this.cleanup();
  }

  private async checkMicrophonePermission() {
    try {
      const permissionStatus = await navigator.permissions.query({ name: 'microphone' as PermissionName });
      if (permissionStatus.state === 'denied') {
        this.isDisabled = true;
        this.state = 'error';
      }
    } catch (error) {
      // Fallback for browsers that don't support permissions API
      console.warn('Permissions API not supported');
    }
  }

  async onButtonClick() {
    if (this.isDisabled) return;

    switch (this.state) {
      case 'idle':
        await this.startRecording();
        break;
      case 'recording':
        await this.stopRecording();
        break;
      case 'error':
        // Reset to idle on error click
        this.state = 'idle';
        break;
    }
  }

  private async startRecording() {
    try {
      this.stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 44100
        }
      });

      this.mediaRecorder = new MediaRecorder(this.stream, {
        mimeType: this.getSupportedMimeType()
      });

      this.audioChunks = [];
      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          this.audioChunks.push(event.data);
        }
      };

      this.mediaRecorder.onstop = async () => {
        await this.processRecording();
      };

      this.mediaRecorder.start();
      this.state = 'recording';
      this.recordingStartTime = Date.now();
      this.startDurationTimer();

    } catch (error) {
      console.error('Error starting recording:', error);
      this.state = 'error';
      this.transcriptionError.emit('Microphone access denied. Please check your browser settings.');
    }
  }

  private async stopRecording() {
    if (this.mediaRecorder && this.state === 'recording') {
      this.mediaRecorder.stop();
      this.state = 'processing';
      this.stopDurationTimer();

      // Stop all tracks
      if (this.stream) {
        this.stream.getTracks().forEach(track => track.stop());
        this.stream = null;
      }
    }
  }

  private async processRecording() {
    try {
      const audioBlob = new Blob(this.audioChunks, { type: this.mediaRecorder?.mimeType || 'audio/webm' });

      // Send to STT service
      this.voiceService.stt(audioBlob).subscribe({
        next: (result) => {
          if (result.text && result.text.trim()) {
            this.transcribedText.emit(result.text);
            this.state = 'idle';
          } else {
            throw new Error('No speech detected');
          }
        },
        error: (error) => {
          console.error('STT error:', error);
          this.state = 'error';
          this.transcriptionError.emit('Couldn\'t transcribe audio. Please try again.');
        }
      });

    } catch (error) {
      console.error('Error processing recording:', error);
      this.state = 'error';
      this.transcriptionError.emit('Failed to process recording. Please try again.');
    }
  }

  private startDurationTimer() {
    this.durationInterval = setInterval(() => {
      this.recordingDuration = Math.floor((Date.now() - this.recordingStartTime) / 1000);

      // Auto-stop after 60 seconds
      if (this.recordingDuration >= 60) {
        this.stopRecording();
      }
    }, 100);
  }

  private stopDurationTimer() {
    if (this.durationInterval) {
      clearInterval(this.durationInterval);
      this.durationInterval = null;
    }
    this.recordingDuration = 0;
  }

  private getSupportedMimeType(): string {
    const types = [
      'audio/webm;codecs=opus',
      'audio/webm',
      'audio/mp4',
      'audio/wav'
    ];

    for (const type of types) {
      if (MediaRecorder.isTypeSupported(type)) {
        return type;
      }
    }

    return 'audio/webm'; // fallback
  }

  private cleanup() {
    this.stopDurationTimer();

    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop());
      this.stream = null;
    }

    if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
      this.mediaRecorder.stop();
    }
  }

  private getAriaLabel(): string {
    switch (this.state) {
      case 'idle': return 'Start voice recording';
      case 'recording': return 'Stop voice recording';
      case 'processing': return 'Processing voice input';
      case 'error': return 'Voice recording error - click to retry';
      default: return 'Voice input';
    }
  }
}