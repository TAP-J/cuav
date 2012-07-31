#!/usr/bin/env python
'''CanberraUAV utility functions for dealing with image regions'''

import numpy, sys, os, time, cuav_util, cv

class Region:
	'''a object representing a recognised region in an image'''
	def __init__(self, x1, y1, x2, y2):
		self.x1 = x1
		self.y1 = y1
		self.x2 = x2
		self.y2 = y2
		self.latlon = None
		self.score = None

        def tuple(self):
            '''return the boundary as a tuple'''
            return (self.x1, self.y1, self.x2, self.y2)

def RegionsConvert(rlist):
	'''convert a region list from tuple to Region format'''
	ret = []
	for r in rlist:
		(x1,y1,x2,y2) = r
		ret.append(Region(x1,y1,x2,y2))
	return ret

def hsv_score(hsv):
	'''try to score a HSV image based on how "interesting" it is for joe detection'''
	(width,height) = cv.GetSize(hsv)
	score = 0
	for x in range(width):
		for y in range(height):
			(h,s,v) = hsv[y,x]
			if h < 22 and s > 50:
				score += 3
				#print h,s,v,'B'
			if h > 120 and h < 200:
				score += 1
				#print h,s,v,'R'
			if v > 160 and s > 100:
				score += (v-160)/10
				#print h,s,v,'V'
			if h>70 and s > 110 and v > 50:
				score += 2
				#print h,s,v,'S'
		return score

def filter_regions(img, regions, min_score=4):
	'''filter a list of regions using HSV values'''
	ret = []
	img = cv.GetImage(cv.fromarray(img))
	for r in regions:
		cv.SetImageROI(img, (r.x1, r.y1, r.x2-r.x1,r.y2-r.y1))
		hsv = cv.CreateImage((r.x2-r.x1,r.y2-r.y1), 8, 3)
		cv.CvtColor(img, hsv, cv.CV_RGB2HSV)
		cv.ResetImageROI(img)
		r.score = hsv_score(hsv)
		if r.score >= min_score:
			ret.append(r)
	return ret


def filter_boundary(regions, boundary, pos=None):
	'''filter a list of regions using a search boundary'''
        ret = []
        for r in regions:
	    if pos is not None and pos.altitude < 10:
	        continue
	    print pos
            if r.latlon is None or cuav_util.polygon_outside(r.latlon, boundary):
                continue
            ret.append(r)
        return ret
    
