%%%%%%%%%%%%%%%%IMAGE SEGMENTATION PROCESS %%%%%%%%%%%%%%%%
clc
clear
img_color=imread('C:\Users\James\Documents\BAH\IdeaFest_2012\Image_Processing\Matlab\Images\image_140.bmp');	%load image
img_gray=rgb2gray(img_color);				% color to gray scale
img_gray_filtered=medfilt2(img_gray, [50 50]);		% apply 50x50 median filter - need to make filter variable

[lehisto x]=imhist(img_gray_filtered);
[level]=triangle_th(lehisto,256);			% apply triangle filter based on
img_BW=im2bw(img_gray_filtered,level);
%
%
%
%Show Results
figure(1)
%Input image
subplot(2,3,1); imshow(img_color); axis off; title('Input Image');
%B/W Image
subplot(2,3,2); imshow(img_gray); axis off; title('B/W Image');
%Filtered Image
subplot(2,3,3); imshow(img_gray_filtered); axis off; title('Filtered Image');
%B/W Image
subplot(2,3,4); imshow(img_BW); axis off; title('B/W Image');
%
%
%%%%%%%%%%%%%%%%SHAPE EXTRACTION PROCESS %%%%%%%%%%%%%%%%
img_BW_no_holes=imfill(img_BW, 'holes');		% fill holes
%img_BW_no_holes_labeled=bwlabel(img_BW_no_holes);	
img_BW_diff = img_BW_no_holes-img_BW;
%img_BW_diff_labeled=logical(img_BW_diff);

% area_measurements = regionprops(img_BW_diff,'Area');
% allAreas = [area_measurements.Area];
% biggestBlobIndex = find(allAreas == max(allAreas));
% keeperBlobsImage = ismember(img_BW_diff, biggestBlobIndex);
% measurements = regionprops(keeperBlobsImage,'MajorAxisLength','MinorAxisLength');

% Display the original color image with outline
% subplot(2,3,5);
% imshow(img_color);
% hold on;
% title('Original Color Image with Outline');
% boundaries = bwboundaries(keeperBlobsImage);
% blobBoundary = boundaries{1};
% plot(blobBoundary(:,2), blobBoundary(:,1), 'g-', 'LineWidth', 1);
% hold off;

%*********************************************
%*****Go through each hole detected*******
%*********************************************
cc=bwconncomp(img_BW_diff);     % Finds number of connected components
s=regionprops(cc,'PixelIdxList','Centroid','Area','MajorAxisLength','MinorAxisLength','Eccentricity','Orientation');
for k=1:cc.NumObjects
    s(k).ClassNumber = img_gray(s(k).PixelIdxList(1));
end

% figure(5);
subplot(2,3,5)
imshow(img_color)
[detect_Boundaries,L] = bwboundaries(img_BW_diff,'noholes');
hold on
count=0;
potholes=0;
for k=1:numel(s)
    x=s(k).Centroid(1);
    y=s(k).Centroid(2);
    text(x,y,sprintf('%d',s(k).ClassNumber),'Color', 'r','FontWeight','bold');
%******************************************************
%   Draws Region around identified Potholes of a Certain Size or Eccentricity   
%******************************************************
    if s(k).Eccentricity < 0.99
        boundary=detect_Boundaries{k};
        plot(boundary(:,2), boundary(:,1),'g-','LineWidth',1);
        potholes=potholes+1;
        k;
        %Hole.boundary(k)=
        else
    end
end
hold off
title('Class number of each object')

%*********************************************
%*****  TEXTURE EXTRACTION AND COMPARISON  *******
%*********************************************
%   variables of interest
%
%   detect_Boundaries: has the boundary locations for each detect 
%   s(k): has the properties of each detection; (may need to recount s(k)
%   to s(potholes). To do so may need to initialize potholes at 1 instead
%   of 0.
%   s(k).Centroid(1,2) has the x,y coordinates needed to get texture
%   interior to pothole

