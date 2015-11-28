from flaskapp import db
import models
from ImageFile import ImageFile
from features import feature_histogram, trim, zoning_method

zeros = ['0-00a.bmp', '0-00b.bmp', '0-00c.bmp', '0-00d.bmp', '0-00e.bmp']
ones = ['1-00a.bmp', '1-00b.bmp', '1-00c.bmp', '1-00d.bmp', '1-00e.bmp']
for j in range(2):
	if j == 0:
		path = "./images/zero/" + zeros[j]
		s = models.Symbol(name="zero")
	else:
		path = "./images/one/" + ones[j]
		s = models.Symbol(name="one")
	db.session.add(s)
	db.session.commit()
    print "added " + s.name
	for i in range(5):
		img = ImageFile(path)
		trimmed = trim(img)
    	img_vector = zoning_method(trimmed)

    	for k in range(16):
    		if k == 0:
    			v = models.V1(histogram_value=img_vector[k])
    		elif k == 1:
    			v = models.V2(histogram_value=img_vector[k])
    		elif k == 2:
    			v = models.V3(histogram_value=img_vector[k])
    		elif k == 3:
    			v = models.V4(histogram_value=img_vector[k])
    		elif k == 4:
    			v = models.V5(histogram_value=img_vector[k])
    		elif k == 5:
    			v = models.V6(histogram_value=img_vector[k])
    		elif k == 6:
    			v = models.V7(histogram_value=img_vector[k])
    		elif k == 7:
    			v = models.V8(histogram_value=img_vector[k])
    		elif k == 8:
    			v = models.V9(histogram_value=img_vector[k])
    		elif k == 9:
    			v = models.V10(histogram_value=img_vector[k])
    		elif k == 10:
    			v = models.V11(histogram_value=img_vector[k])
    		elif k == 11:
    			v = models.V12(histogram_value=img_vector[k])
    		elif k == 12:
    			v = models.V13(histogram_value=img_vector[k])
    		elif k == 13:
    			v = models.V14(histogram_value=img_vector[k])
    		elif k == 14:
    			v = models.V15(histogram_value=img_vector[k])
    		elif k == 15:
    			v = models.V16(histogram_value=img_vector[k])
    		db.session.add(v)
            print "added" + str(v.histogram_value)
    		db.session.commit()


