def dense(w, s):
	if w + s == 0:
		return 0
	return s / (w + s)

def resolve():
	a, b, c, d, e, f = map(int, input().split())
	water_set = set()
	sugar_set = set()
	for i in range(31):
		for j in range(31):
			s = 100*a*i + 100*b*j
			if s <= f:
				water_set.add(100*a*i + 100*b*j)
	for i in range(1001):
		for j in range(1001):
			s = i*c + j*d
			if s <= f:
				sugar_set.add(s)
	wv, sv = 0, 0
	for w in water_set:
		for s in sugar_set:
			if f < (w + s) or (w//100*e) < s:
				continue
			if dense(wv, sv) <= dense(w, s):
				wv, sv = w, s
	print(wv+sv, sv)
resolve()