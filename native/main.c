#include "main.h"

typedef unsigned int 		uint32;
typedef unsigned long long 	uint64;
typedef unsigned short		uint16;
typedef unsigned char		uint8;

int _stdcall DllMain(uint32 hInstance, uint32 reason, uint32 reserved)
{
	switch (reason) 
	{
		case 1:		/* loading */
		case 0:		/* unloading */
		case 2:		/* thread attach */
		case 3:		/* thread detach */
			break;
	}
	return 1;
}

/*
	Decodes RAW DXT1 image data. So you need to know the decoded width and height. Or, the
	encoded width and height and just multiply both by 4. It is fast, but there is room for
	improvement I am sure. Especially, if you can use processor extensions for math, and 
	possibly even find bad programming where the compiler is unable to optimize it out.

	But, overall, it is fast compared to Python!
*/
int __declspec(dllexport) _stdcall DXT1_decode(void *in, uint32 l, uint32 w, uint32 h, void *out)
{
	uint16		*pin;
	uint16		*pout;
	uint32		ndx;
	uint16		c1, c2, c3, c4, _c1, _c4;
	uint8		c1r, c1g, c1b;
	uint8		c2r, c2g, c2b;
	uint8		c3r, c3g, c3b;
	uint8		c4r, c4g, c4b;
	uint8		tr, tg, tb;
	uint32		i;
	uint8		z;
	uint32		col, row, x, y;
	uint32		bw, bh;

	pout = (uint16*)out;

	bw = w >> 2;
	bh = h >> 2;
	pin = (uint16*)in;		
	l = l / 8;			// the number of blocks (64-bit representations of 16x16 pixel blocks)
	for (i = 0; i < l; ++i)
	{
		// indexing is done in 1/4 of block address 16-bit/64-bit 
		// so we multiply by 4 so we actually access the first
		// 16-bit of each block
		c1 = pin[i * 4 + 0];
		c4 = pin[i * 4 + 1];
		ndx = pin[i * 4 + 2] | (pin[i * 4 + 3] << 16);
		_c1 = c1;
		_c4 = c4;
		c1b = c1 & 0x1f;
		c1 = c1 >> 5;
		c1g = c1 & 0x3f;
		c1 = c1 >> 6;
		c1r = c1 & 0x1f;
		c4b = c4 & 0x1f;
		c4 = c4 >> 5;
		c4g = c4 & 0x3f;
		c4 = c4 >> 6;
		c4r = c4 & 0x1f;
		tr = c4r - c1r;
		tg = c4g - c1g;
		tb = c4b - c1b;
		c1 = _c1;
		c4 = _c4;
		c2r = (tr / 3) + c1r;
		c2g = (tg / 3) + c1g;
		c2b = (tb / 3) + c1b;
		c3r = ((tr / 3) * 2) + c1r;
		c3g = ((tg / 3) * 2) + c1g;
		c3b = ((tb / 3) * 2) + c1b;
		// block width is different than decoded image width
		y = i / bw;
		x = i - (y * bw);
		// now we transform into pixel coordinates, thus << 2.
		y = y << 2;
		x = x << 2;
		for (z = 0; z < 16; ++z)
		{
			col = (z & 0x3) + x;
			row = ((z & 0xc) >> 2) + y;
			switch (ndx & 0x3)
			{
				case 0:
					pout[row * w + col] = c1;
					//pout[row * w + col] = (c1r << 16) | (c1g << 8) | c1b;
					break;
				case 1:
					pout[row * w + col] = (c2r << (6 + 5)) | (c2g << 5) | c2b;
					//pout[row * w + col] = (c2r << 16) | (c2g << 8) | c2b;
					//pout[row * w + col] = 0;
					break;
				case 2:
					pout[row * w + col] = (c3r << (6 + 5)) | (c3g << 5) | c3b;
					//pout[row * w + col] = (c3r << 16) | (c3g << 8) | c3b;
					//pout[row * w + col] = 0;
					break;
				case 3:
					pout[row * w + col] = c4;
					//pout[row * w + col] = (c4r << 16) | (c4g << 8) | c4b;
					break;				
			}
			ndx = ndx >> 2;
		}
	}

	return 0;
}
