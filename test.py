# -*- coding: utf-8 -*-
import numpy
import sympy
import matplotlib.pyplot as plt

# precition
sympy.mpmath.mp.prec = 256

#
def cascade_wavelet(phi, gg):
	x = [k/128.0 - 3 for k in range((128*7))]
	sqrt2 = sympy.mpmath.sqrt(2)

	psi = [0.0]*(128*7)
	for k,g in enumerate(gg):
		for i in range(len(psi)):
			if 0 <= 2*i-128*k and 2*i-128*k < len(phi):
				psi[i] += sqrt2*g*phi[2*i-128*k]
	return x, psi
#
def cascade_scaling(h):
	phi =  numpy.array( [1.0/(len(h)-1)]*(len(h)-1)*128 )
	center = (len(h)-1)/2
	x = [k/128.0 - center for k in range(len(phi))]
	sqrt2 = sympy.mpmath.sqrt(2)

	for _ in range(100):
		phi2 = numpy.array( [0.0]*len(phi) )
		for k,hk in enumerate(h):
			for i in range(len(phi)):
				if 0 <= 2*i-128*k and 2*i-128*k < len(phi):
					phi2[i] += sqrt2*hk*phi[2*i-128*k]

		if numpy.linalg.norm( phi - phi2 ) < 1.0e-10:
			return x, phi2
		else:
			phi = phi2
	else:
		raise Exception

def cdf_9_7():
	# 多項式を作成する q(y) = 20y^3 + 10*y^2 + 4*y + 1
	qy = [sympy.mpmath.binomial(4-1+k,k) for k in [3,2,1,0]]

	# q(y) = 0 を解く
	y = sympy.mpmath.polyroots(qy)
	
	# y[0]: -0.3423840948
	# y[1]: -0.0788079525 + 0.3739306454j
	# y[2]: -0.0788079525 - 0.3739306454j

	# 実数解からなる因子を使用して多項式を作成
	h0z = sympy.sympify('-sqrt(2.0)*(y-y0)/y0') \
	           .subs({'y':'-1/4*z+1/2-1/4/z', 'y0':y[0]})

	# vanising momentsを適用
	hz = (sympy.sympify('z**(-2)*((z+1)/2)**4')*h0z).expand()
	
	# scaling係数を取得
	scaling_coeff = [hz.coeff('z',k) for k in [-3,-2,-1,0,1,2,3]]

	# 共役複素数解からなる因子を使用して多項式を作成
	d_h0z = sympy.sympify('sqrt(2.0)*(y-y1)/y1*(y-y2)/y2') \
	             .subs({'y':'-1/4*z+1/2-1/4/z', 'y1':y[1], 'y2':y[2]})

	# vanising momentsを適用
	d_hz = (sympy.sympify('z**(-2)*((z+1)/2)**4')*d_h0z).expand()

	# dual scaling係数を取得
	d_scaling_coeff = [sympy.re(d_hz.coeff('z',k)) for k in [-4,-3,-2,-1,0,1,2,3,4]]
	
	# wavelet係数を取得
	wavelet_coeff = [s*(-1)**k for k,s in zip([-4,-3,-2,-1,0,1,2,3,4], d_scaling_coeff)]

	# dual wavelet係数を取得
	d_wavelet_coeff = [s*(-1)**k for k,s in zip([-3,-2,-1,0,1,2,3], scaling_coeff) ]

	return scaling_coeff, d_scaling_coeff, wavelet_coeff, d_wavelet_coeff

def main():
	scaling, d_scaling, wavelet_coeff, d_wavelet_coeff= cdf_9_7()

	f = open('cdf_9_7_scaling_coefficients.txt', 'w')
	print 'CDF 9/7 scaling coefficients'
	f.write('# CDF 9/7 scaling coefficients\n')
	for i, h in enumerate(scaling):
		sympy.mpmath.nprint(h, 40)
		f.write('h['+ str(i) + ']='+ sympy.mpmath.nstr(h, 40) + '\n')
	f.close()
	
	f = open('cdf_9_7_dual_scaling_coefficients.txt', 'w')
	print '\nCDF 9/7 dual scaling coefficients'
	f.write('# CDF 9/7 dual scaling coefficients\n')
	for i, h in enumerate(d_scaling):
		sympy.mpmath.nprint(h, 40)
		f.write('h['+ str(i) + ']='+ sympy.mpmath.nstr(h, 40) + '\n')
	f.close()
	
	print '\nCDF 9/7 wavelet coefficients'
	for i, h in enumerate(wavelet_coeff):
		sympy.mpmath.nprint(h, 40)
	
	print '\nCDF 9/7 dual wavelet coefficients'
	for i, h in enumerate(d_wavelet_coeff):
		sympy.mpmath.nprint(h, 40)
	
	x, phi1 = cascade_scaling(scaling)
	plt.plot(x, phi1)

	x, phi2 = cascade_scaling(d_scaling)
	plt.plot(x, phi2)

	plt.grid()
	plt.legend(['CDF9/7 scaling', 'CDF9/7 dual scaling'])
	#plt.show()
	plt.savefig('cdf_9_7_scaling.png')
	plt.clf()

	x, psi1 = cascade_wavelet(phi1, wavelet_coeff)
	plt.plot(x, psi1)

	x, psi2 = cascade_wavelet(phi2, d_wavelet_coeff)
	plt.plot(x, psi2)

	plt.grid()
	plt.legend(['CDF9/7 wavelet', 'CDF9/7 dual wavelet'])
	#plt.show()
	plt.savefig('cdf_9_7_wavelet.png')
	plt.clf()

if __name__ == '__main__':
	main()
