import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { ArrowUpTrayIcon, PencilSquareIcon } from '@heroicons/react/24/outline';

const InitialChoiceStep = ({ onUploadClick, onCreateClick }) => {
  return (
    <div className="grid md:grid-cols-2 gap-6">
      <Card className="cursor-pointer hover:border-indigo-500 transition-colors" onClick={onUploadClick}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ArrowUpTrayIcon className="w-6 h-6 text-indigo-500" />
            Upload Resume
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-600">
            Upload an existing resume in PDF or DOCX format. We'll help you optimize it for your target job.
          </p>
        </CardContent>
      </Card>

      <Card className="cursor-pointer hover:border-indigo-500 transition-colors" onClick={onCreateClick}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <PencilSquareIcon className="w-6 h-6 text-indigo-500" />
            Create New Resume
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-600">
            Build your resume from scratch using our guided form. Perfect for creating a tailored professional resume.
          </p>
        </CardContent>
      </Card>
    </div>
  );
};

export default InitialChoiceStep;