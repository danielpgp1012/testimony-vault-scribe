
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { FileAudio, Upload, Search, Filter, FileText } from 'lucide-react';

const AboutPage = () => {
  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <h1 className="text-2xl font-bold md:text-3xl">About Testimony Vault</h1>
        <p className="text-muted-foreground">
          Learn how this application helps preserve and search church testimonies
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2">
              <Upload className="h-5 w-5 text-primary" />
              Easy Upload
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Drag and drop MP3 recordings of testimonies along with metadata like speaker name, date, and tags.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2">
              <FileAudio className="h-5 w-5 text-primary" />
              Automatic Transcription
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Recordings are automatically transcribed using advanced speech recognition technology for accurate text.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2">
              <Search className="h-5 w-5 text-primary" />
              Powerful Search
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Search through transcripts using keywords or phrases to easily find specific testimonies.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2">
              <Filter className="h-5 w-5 text-primary" />
              Advanced Filtering
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Filter testimonies by speaker, date, tags, or transcription status to find exactly what you need.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-primary" />
              Secure Storage
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              All testimonies are securely stored in both Google Drive and our database for redundancy and easy access.
            </p>
          </CardContent>
        </Card>
      </div>

      <Card className="mt-6">
        <CardHeader>
          <CardTitle>How It Works</CardTitle>
        </CardHeader>
        <CardContent>
          <ol className="space-y-4 list-decimal list-inside text-sm">
            <li>
              <span className="font-medium">Upload</span>: Drag and drop an MP3 file and fill in the metadata.
            </li>
            <li>
              <span className="font-medium">Storage</span>: The file is securely uploaded to both Google Drive and our storage.
            </li>
            <li>
              <span className="font-medium">Processing</span>: Our system automatically begins transcribing the audio.
            </li>
            <li>
              <span className="font-medium">Indexing</span>: The transcript is indexed for searching and semantic queries.
            </li>
            <li>
              <span className="font-medium">Access</span>: Access transcribed testimonies through the dashboard or search function.
            </li>
          </ol>
        </CardContent>
      </Card>

      <div className="text-center text-sm text-muted-foreground pt-6">
        <p>Testimony Vault © {new Date().getFullYear()}</p>
        <p className="mt-1">A tool for preserving and sharing church testimonies</p>
      </div>
    </div>
  );
};

export default AboutPage;
