'use client';

import { useState, useRef } from 'react';
import { Play, Pause, Volume2, VolumeX, Maximize, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

interface VideoPlayerProps {
  src: string;
  poster?: string;
  className?: string;
}

// Extract video ID from various URL formats
function getEmbedUrl(url: string): { type: 'embed' | 'native'; url: string } {
  // YouTube
  const youtubeMatch = url.match(
    /(?:youtube\.com\/(?:watch\?v=|embed\/|v\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})/
  );
  if (youtubeMatch) {
    return {
      type: 'embed',
      url: `https://www.youtube.com/embed/${youtubeMatch[1]}?rel=0`,
    };
  }

  // Vimeo
  const vimeoMatch = url.match(/vimeo\.com\/(?:video\/)?(\d+)/);
  if (vimeoMatch) {
    return {
      type: 'embed',
      url: `https://player.vimeo.com/video/${vimeoMatch[1]}`,
    };
  }

  // Twitter/X video (just link, can't embed directly)
  if (url.includes('twitter.com') || url.includes('x.com')) {
    return { type: 'embed', url };
  }

  // Direct video file
  return { type: 'native', url };
}

export function VideoPlayer({ src, poster, className }: VideoPlayerProps) {
  const { type, url } = getEmbedUrl(src);
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(false);
  const [showControls, setShowControls] = useState(true);

  const togglePlay = () => {
    if (!videoRef.current) return;
    if (isPlaying) {
      videoRef.current.pause();
    } else {
      videoRef.current.play();
    }
    setIsPlaying(!isPlaying);
  };

  const toggleMute = () => {
    if (!videoRef.current) return;
    videoRef.current.muted = !isMuted;
    setIsMuted(!isMuted);
  };

  const toggleFullscreen = () => {
    if (!videoRef.current) return;
    if (document.fullscreenElement) {
      document.exitFullscreen();
    } else {
      videoRef.current.requestFullscreen();
    }
  };

  // Embedded video (YouTube, Vimeo)
  if (type === 'embed') {
    return (
      <div className={cn('aspect-video bg-black rounded-md overflow-hidden', className)}>
        <iframe
          src={url}
          className="w-full h-full"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
          title="Video evidence"
        />
      </div>
    );
  }

  // Native HTML5 video
  return (
    <div
      className={cn(
        'relative aspect-video bg-black rounded-md overflow-hidden group',
        className
      )}
      onMouseEnter={() => setShowControls(true)}
      onMouseLeave={() => !isPlaying && setShowControls(true)}
    >
      {isLoading && !error && (
        <div className="absolute inset-0 flex items-center justify-center bg-muted">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      )}

      {error && (
        <div className="absolute inset-0 flex flex-col items-center justify-center bg-muted">
          <p className="text-sm text-muted-foreground mb-2">Unable to load video</p>
          <a
            href={src}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-primary hover:underline"
          >
            Open in new tab
          </a>
        </div>
      )}

      <video
        ref={videoRef}
        src={url}
        poster={poster}
        className="w-full h-full object-contain"
        onLoadedData={() => setIsLoading(false)}
        onError={() => {
          setIsLoading(false);
          setError(true);
        }}
        onPlay={() => setIsPlaying(true)}
        onPause={() => setIsPlaying(false)}
        onEnded={() => setIsPlaying(false)}
        playsInline
        preload="metadata"
      />

      {/* Custom Controls */}
      {!error && (
        <div
          className={cn(
            'absolute bottom-0 left-0 right-0 p-3 bg-gradient-to-t from-black/80 to-transparent transition-opacity',
            showControls || !isPlaying ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'
          )}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <button
                onClick={togglePlay}
                className="p-1.5 rounded-full bg-white/20 hover:bg-white/30 transition-colors"
                aria-label={isPlaying ? 'Pause' : 'Play'}
              >
                {isPlaying ? (
                  <Pause className="h-4 w-4 text-white" />
                ) : (
                  <Play className="h-4 w-4 text-white" />
                )}
              </button>
              <button
                onClick={toggleMute}
                className="p-1.5 rounded-full bg-white/20 hover:bg-white/30 transition-colors"
                aria-label={isMuted ? 'Unmute' : 'Mute'}
              >
                {isMuted ? (
                  <VolumeX className="h-4 w-4 text-white" />
                ) : (
                  <Volume2 className="h-4 w-4 text-white" />
                )}
              </button>
            </div>
            <button
              onClick={toggleFullscreen}
              className="p-1.5 rounded-full bg-white/20 hover:bg-white/30 transition-colors"
              aria-label="Fullscreen"
            >
              <Maximize className="h-4 w-4 text-white" />
            </button>
          </div>
        </div>
      )}

      {/* Click to play overlay */}
      {!isPlaying && !error && !isLoading && (
        <button
          onClick={togglePlay}
          className="absolute inset-0 flex items-center justify-center bg-black/30 hover:bg-black/40 transition-colors"
          aria-label="Play video"
        >
          <div className="p-4 rounded-full bg-white/90 hover:bg-white transition-colors">
            <Play className="h-8 w-8 text-black" />
          </div>
        </button>
      )}
    </div>
  );
}
