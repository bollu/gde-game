ZIPNAME=20161105_20161047
.PHONY: zip
zip:
	@rm -rf $(ZIPNAME)
	mkdir -p $(ZIPNAME)
	cp  links.txt README.md \
		screenshot.png \
		feedback1.jpg feedback2.jpg Game-design-document.docx \
		team-photo.jpg \
		$(ZIPNAME) 
	zip -r $(ZIPNAME).zip $(ZIPNAME)
