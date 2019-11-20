ZIPNAME=20161105_20161047
.PHONY: zip
zip:
	@rm -rf $(ZIPNAME)
	mkdir -p $(ZIPNAME)
	cp  game.py immigrant_names.txt links.txt makefile README.md \
		render_png_2.py render_png.py requirements.txt screenshot.png \
		feedback1.jpg feedback2.jpg Game-design-document.docx \
		team-photo.jpg \
		$(ZIPNAME) 
	zip -r $(ZIPNAME).zip $(ZIPNAME)
